"""
Integration tests for MSA wrapper functionality with real FLEx data.

This module contains integration tests that verify MSA wrappers work correctly
with actual FLEx projects. These tests require a FLEx project to be available
and use the full FlexLibs2 API.

Tests verify:
- MSA wrapping from actual entry MSA collections
- Type detection with real FLEx objects
- Filtering with real POS objects
- Integration with other FlexLibs2 operations
- Backward compatibility with existing code
"""

import pytest


class TestMSAIntegration:
    """Integration tests for MSA wrappers with real FLEx data."""

    @pytest.mark.skip(reason="Requires FLEx project initialization")
    def test_wrap_entry_msas(self, flex_project):
        """Test wrapping MSAs from a real entry."""
        from flexlibs2.code.Lexicon.morphosyntax_analysis import MorphosyntaxAnalysis
        from flexlibs2.code.Lexicon.msa_collection import MSACollection

        # Get an entry with MSAs
        entry = flex_project.lp.LexDB.Entries[0]

        if not entry.MorphoSyntaxAnalysesOC.Count:
            pytest.skip("Test entry has no MSAs")

        # Wrap MSAs
        msas = MSACollection([
            MorphosyntaxAnalysis(msa)
            for msa in entry.MorphoSyntaxAnalysesOC
        ])

        # Verify wrapping worked
        assert len(msas) == entry.MorphoSyntaxAnalysesOC.Count
        assert isinstance(msas, MSACollection)

    @pytest.mark.skip(reason="Requires FLEx project initialization")
    def test_msa_type_detection(self, flex_project):
        """Test that type detection works with real MSAs."""
        from flexlibs2.code.Lexicon.morphosyntax_analysis import MorphosyntaxAnalysis

        # Get entries and look for different MSA types
        found_stem = False
        found_deriv = False
        found_infl = False

        for entry in flex_project.lp.LexDB.Entries:
            if found_stem and found_deriv and found_infl:
                break

            for msa in entry.MorphoSyntaxAnalysesOC:
                wrapped = MorphosyntaxAnalysis(msa)

                if wrapped.is_stem_msa:
                    found_stem = True
                    assert wrapped.class_type == 'MoStemMsa'
                    assert not wrapped.is_deriv_aff_msa
                    assert not wrapped.is_infl_aff_msa

                elif wrapped.is_deriv_aff_msa:
                    found_deriv = True
                    assert wrapped.class_type == 'MoDerivAffMsa'
                    assert wrapped.is_deriv_aff_msa
                    assert not wrapped.is_stem_msa

                elif wrapped.is_infl_aff_msa:
                    found_infl = True
                    assert wrapped.class_type == 'MoInflAffMsa'
                    assert wrapped.is_infl_aff_msa
                    assert not wrapped.is_stem_msa

        # At least some types should be found in typical projects
        # (though we'll skip if none are found)
        if not (found_stem or found_deriv or found_infl):
            pytest.skip("No MSA types found in test project")

    @pytest.mark.skip(reason="Requires FLEx project initialization")
    def test_msa_pos_access(self, flex_project):
        """Test accessing POS through wrapper."""
        from flexlibs2.code.Lexicon.morphosyntax_analysis import MorphosyntaxAnalysis
        from flexlibs2.code.Lexicon.msa_collection import MSACollection

        # Get MSAs
        msas = []
        for entry in flex_project.lp.LexDB.Entries:
            for msa in entry.MorphoSyntaxAnalysesOC:
                msas.append(MorphosyntaxAnalysis(msa))
            if len(msas) >= 10:
                break

        if not msas:
            pytest.skip("No MSAs found in test project")

        collection = MSACollection(msas)

        # Test accessing pos_main
        for msa in collection:
            pos = msa.pos_main

            # POS may be None, but accessing it should not fail
            if pos is not None:
                # Should have name accessible
                assert hasattr(pos, 'Name')
                assert hasattr(pos, 'Guid')

    @pytest.mark.skip(reason="Requires FLEx project initialization")
    def test_msa_filtering(self, flex_project):
        """Test filtering MSAs with real data."""
        from flexlibs2.code.Lexicon.morphosyntax_analysis import MorphosyntaxAnalysis
        from flexlibs2.code.Lexicon.msa_collection import MSACollection

        # Collect all MSAs
        all_msas = []
        for entry in flex_project.lp.LexDB.Entries:
            for msa in entry.MorphoSyntaxAnalysesOC:
                all_msas.append(MorphosyntaxAnalysis(msa))
            if len(all_msas) >= 20:
                break

        if len(all_msas) < 5:
            pytest.skip("Not enough MSAs for filtering test")

        collection = MSACollection(all_msas)

        # Test type filtering
        stem_msas = collection.stem_msas()
        deriv_msas = collection.deriv_aff_msas()
        infl_msas = collection.infl_aff_msas()

        # Filtered collections should be valid (but may be empty)
        assert isinstance(stem_msas, MSACollection)
        assert isinstance(deriv_msas, MSACollection)
        assert isinstance(infl_msas, MSACollection)

        # Sum of type-specific should not exceed total
        total_by_type = len(stem_msas) + len(deriv_msas) + len(infl_msas)
        assert total_by_type <= len(collection)

    @pytest.mark.skip(reason="Requires FLEx project initialization")
    def test_msa_filtering_with_pos(self, flex_project):
        """Test filtering MSAs by POS."""
        from flexlibs2.code.Lexicon.morphosyntax_analysis import MorphosyntaxAnalysis
        from flexlibs2.code.Lexicon.msa_collection import MSACollection

        # Get MSAs with POS
        all_msas = []
        for entry in flex_project.lp.LexDB.Entries:
            for msa in entry.MorphoSyntaxAnalysesOC:
                wrapped = MorphosyntaxAnalysis(msa)
                if wrapped.pos_main is not None:
                    all_msas.append(wrapped)
            if len(all_msas) >= 10:
                break

        if len(all_msas) < 5:
            pytest.skip("Not enough MSAs with POS for filtering test")

        collection = MSACollection(all_msas)

        # Test has_pos filter
        with_pos = collection.filter(has_pos=True)
        assert len(with_pos) == len(collection)  # All should have POS

        without_pos = collection.filter(has_pos=False)
        assert len(without_pos) == 0  # None should lack POS

        # Test filtering by specific POS
        if len(all_msas) > 0 and all_msas[0].pos_main:
            target_pos = all_msas[0].pos_main
            matching = collection.filter(pos_main=target_pos)

            # All matched should have matching POS
            for msa in matching:
                assert msa.pos_main is not None
                assert str(msa.pos_main.Guid) == str(target_pos.Guid)

    @pytest.mark.skip(reason="Requires FLEx project initialization")
    def test_msa_collection_display(self, flex_project):
        """Test collection string display."""
        from flexlibs2.code.Lexicon.morphosyntax_analysis import MorphosyntaxAnalysis
        from flexlibs2.code.Lexicon.msa_collection import MSACollection

        # Get MSAs
        all_msas = []
        for entry in flex_project.lp.LexDB.Entries:
            for msa in entry.MorphoSyntaxAnalysesOC:
                all_msas.append(MorphosyntaxAnalysis(msa))
            if len(all_msas) >= 10:
                break

        if not all_msas:
            pytest.skip("No MSAs found")

        collection = MSACollection(all_msas)

        # Get string representation
        display = str(collection)

        # Should show collection name and count
        assert "MSACollection" in display
        assert str(len(all_msas)) in display

        # Should show some type breakdown
        if len(all_msas) > 0:
            assert "total" in display.lower()

    @pytest.mark.skip(reason="Requires FLEx project initialization")
    def test_msa_chained_filtering(self, flex_project):
        """Test chaining multiple filters."""
        from flexlibs2.code.Lexicon.morphosyntax_analysis import MorphosyntaxAnalysis
        from flexlibs2.code.Lexicon.msa_collection import MSACollection

        # Get MSAs
        all_msas = []
        for entry in flex_project.lp.LexDB.Entries:
            for msa in entry.MorphoSyntaxAnalysesOC:
                all_msas.append(MorphosyntaxAnalysis(msa))
            if len(all_msas) >= 20:
                break

        if len(all_msas) < 5:
            pytest.skip("Not enough MSAs for chaining test")

        collection = MSACollection(all_msas)

        # Chain: get stems with POS
        stems_with_pos = collection.stem_msas().filter(has_pos=True)

        # Result should be valid
        assert isinstance(stems_with_pos, MSACollection)
        assert len(stems_with_pos) <= len(collection)

        # All should be stems with POS
        for msa in stems_with_pos:
            assert msa.is_stem_msa
            assert msa.pos_main is not None

    @pytest.mark.skip(reason="Requires FLEx project initialization")
    def test_msa_advanced_access(self, flex_project):
        """Test advanced C# interface access."""
        from flexlibs2.code.Lexicon.morphosyntax_analysis import MorphosyntaxAnalysis

        # Find different MSA types
        for entry in flex_project.lp.LexDB.Entries:
            for msa in entry.MorphoSyntaxAnalysesOC:
                wrapped = MorphosyntaxAnalysis(msa)

                # Test as_* methods
                if wrapped.is_stem_msa:
                    concrete = wrapped.as_stem_msa()
                    assert concrete is not None
                    assert wrapped.concrete is not None

                elif wrapped.is_deriv_aff_msa:
                    concrete = wrapped.as_deriv_aff_msa()
                    assert concrete is not None

                # Non-matching as_* should return None
                if not wrapped.is_stem_msa:
                    assert wrapped.as_stem_msa() is None

                if not wrapped.is_deriv_aff_msa:
                    assert wrapped.as_deriv_aff_msa() is None

                # concrete property should always work
                assert wrapped.concrete is not None
                assert hasattr(wrapped.concrete, 'ClassName')

            # Just test a few
            break


class TestMSABackwardCompatibility:
    """Tests for backward compatibility with existing code."""

    def test_collection_iteration_compatibility(self):
        """Test that iteration works with existing patterns."""
        from flexlibs2.code.Lexicon.msa_collection import MSACollection
        from unittest.mock import Mock

        # Create mock MSAs
        msa1 = Mock()
        msa1.class_type = 'MoStemMsa'
        msa1.ClassName = 'MoStemMsa'

        msa2 = Mock()
        msa2.class_type = 'MoDerivAffMsa'
        msa2.ClassName = 'MoDerivAffMsa'

        collection = MSACollection([msa1, msa2])

        # Should work with for loops
        count = 0
        for msa in collection:
            count += 1
        assert count == 2

        # Should work with list()
        as_list = list(collection)
        assert len(as_list) == 2

        # Should work with len()
        assert len(collection) == 2

    def test_collection_slicing_compatibility(self):
        """Test that slicing returns same type."""
        from flexlibs2.code.Lexicon.msa_collection import MSACollection
        from unittest.mock import Mock

        msa1 = Mock(class_type='MoStemMsa', ClassName='MoStemMsa')
        msa2 = Mock(class_type='MoDerivAffMsa', ClassName='MoDerivAffMsa')
        msa3 = Mock(class_type='MoInflAffMsa', ClassName='MoInflAffMsa')

        collection = MSACollection([msa1, msa2, msa3])

        # Slicing should return MSACollection
        sliced = collection[0:2]
        assert isinstance(sliced, MSACollection)
        assert len(sliced) == 2

    def test_filter_returns_same_type(self):
        """Test that filters return MSACollection."""
        from flexlibs2.code.Lexicon.msa_collection import MSACollection
        from unittest.mock import Mock

        msa1 = Mock(class_type='MoStemMsa', ClassName='MoStemMsa', pos_main=None)
        msa2 = Mock(class_type='MoDerivAffMsa', ClassName='MoDerivAffMsa', pos_main=Mock())

        collection = MSACollection([msa1, msa2])

        # filter() should return MSACollection
        filtered = collection.stem_msas()
        assert isinstance(filtered, MSACollection)

        # where() should return MSACollection
        where_result = collection.where(lambda m: True)
        assert isinstance(where_result, MSACollection)

        # by_type() should return MSACollection
        by_type_result = collection.by_type('MoStemMsa')
        assert isinstance(by_type_result, MSACollection)
